from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from models.db import db, Log, User, Rule
from services.security_service import admin_required, log_activity
from datetime import datetime, timedelta
import json

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('', methods=['GET'])
@jwt_required()
def get_logs():
    """
    Get logs with filtering, pagination, and search
    ---
    tags:
      - Logs
    security:
      - JWT: []
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number
      - name: per_page
        in: query
        type: integer
        required: false
        default: 50
        description: Items per page (max 100)
      - name: event_type
        in: query
        type: string
        required: false
        description: Filter by event type (e.g., 'FIREWALL', 'AUTH', 'RULES')
      - name: level
        in: query
        type: string
        required: false
        description: Filter by log level (e.g., 'INFO', 'WARNING', 'ERROR')
      - name: action
        in: query
        type: string
        required: false
        description: Filter by action (e.g., 'ALLOW', 'DENY', 'LOGIN')
      - name: search
        in: query
        type: string
        required: false
        description: Search in log details
      - name: start_date
        in: query
        type: string
        format: date-time
        required: false
        description: Filter logs after this date (ISO 8601 format)
      - name: end_date
        in: query
        type: string
        format: date-time
        required: false
        description: Filter logs before this date (ISO 8601 format)
    responses:
      200:
        description: List of logs with pagination info
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                $ref: '#/definitions/Log'
            total:
              type: integer
              description: Total number of items
            page:
              type: integer
              description: Current page number
            per_page:
              type: integer
              description: Number of items per page
            pages:
              type: integer
              description: Total number of pages
    """
    try:
        # Pagination
        page = max(1, request.args.get('page', 1, type=int))
        per_page = min(100, max(1, request.args.get('per_page', 50, type=int)))
        
        # Base query
        query = Log.query
        
        # Apply filters
        if event_type := request.args.get('event_type'):
            query = query.filter(Log.event_type == event_type.upper())
            
        if level := request.args.get('level'):
            query = query.filter(Log.level == level.upper())
            
        if action := request.args.get('action'):
            query = query.filter(Log.action == action.upper())
            
        if search := request.args.get('search'):
            search_term = f"%{search}%"
            query = query.filter(Log.details.ilike(search_term))
            
        # Date range filter
        if start_date := request.args.get('start_date'):
            try:
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Log.created_at >= start_date)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO 8601 format.'}), 400
                
        if end_date := request.args.get('end_date'):
            try:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Log.created_at <= end_date)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO 8601 format.'}), 400
        
        # Order by most recent first
        query = query.order_by(Log.created_at.desc())
        
        # Execute paginated query
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Format response
        logs = []
        for log in pagination.items:
            log_data = {
                'id': log.id,
                'event_type': log.event_type,
                'level': log.level,
                'source_ip': log.source_ip,
                'destination_ip': log.destination_ip,
                'action': log.action,
                'details': log.details,
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'user': None,
                'rule': None
            }
            
            if log.user:
                log_data['user'] = {
                    'id': log.user.id,
                    'username': log.user.username
                }
                
            if log.rule:
                log_data['rule'] = {
                    'id': log.rule.id,
                    'name': log.rule.name
                }
                
            logs.append(log_data)
        
        return jsonify({
            'items': logs,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching logs: {str(e)}")
        return jsonify({'error': 'Failed to fetch logs'}), 500

@logs_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_log_stats():
    """
    Get log statistics
    ---
    tags:
      - Logs
    security:
      - JWT: []
    parameters:
      - name: days
        in: query
        type: integer
        required: false
        default: 7
        description: Number of days to include in statistics
    responses:
      200:
        description: Log statistics
        schema:
          type: object
          properties:
            total_logs:
              type: integer
            logs_by_type:
              type: object
              additionalProperties:
                type: integer
            logs_by_level:
              type: object
              additionalProperties:
                type: integer
            logs_by_day:
              type: array
              items:
                type: object
                properties:
                  date:
                    type: string
                    format: date
                  count:
                    type: integer
    """
    try:
        days = min(365, max(1, request.args.get('days', 7, type=int)))
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Total logs
        total_logs = Log.query.count()
        
        # Logs by type
        logs_by_type = {
            result[0]: result[1] 
            for result in db.session.query(
                Log.event_type, 
                db.func.count(Log.id)
            ).group_by(Log.event_type).all()
        }
        
        # Logs by level
        logs_by_level = {
            result[0]: result[1] 
            for result in db.session.query(
                Log.level, 
                db.func.count(Log.id)
            ).filter(Log.level.isnot(None)).group_by(Log.level).all()
        }
        
        # Logs by day
        logs_by_day = db.session.query(
            db.func.date(Log.created_at).label('date'),
            db.func.count(Log.id).label('count')
        ).filter(
            Log.created_at >= since_date
        ).group_by(
            db.func.date(Log.created_at)
        ).order_by(
            db.func.date(Log.created_at)
        ).all()
        
        return jsonify({
            'total_logs': total_logs,
            'logs_by_type': logs_by_type,
            'logs_by_level': logs_by_level,
            'logs_by_day': [{'date': str(day[0]), 'count': day[1]} for day in logs_by_day]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching log stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch log statistics'}), 500

@logs_bp.route('', methods=['POST'])
@jwt_required()
def create_log():
    """
    Create a new log entry
    ---
    tags:
      - Logs
    security:
      - JWT: []
    parameters:
      - in: body
        name: log
        description: The log entry to create
        schema:
          type: object
          required:
            - event_type
            - level
          properties:
            event_type:
              type: string
              enum: [FIREWALL, AUTH, RULES, SYSTEM, API]
              description: Type of event
            level:
              type: string
              enum: [DEBUG, INFO, WARNING, ERROR, CRITICAL]
              description: Log level
            source_ip:
              type: string
              description: Source IP address
            destination_ip:
              type: string
              description: Destination IP address
            action:
              type: string
              description: Action taken (e.g., ALLOW, DENY, LOGIN)
            rule_id:
              type: integer
              description: Related rule ID (if any)
            details:
              type: object
              description: Additional log details (will be stored as JSON)
    responses:
      201:
        description: Log entry created successfully
      400:
        description: Invalid input
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['event_type', 'level']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create log entry
        log = Log(
            event_type=data['event_type'].upper(),
            level=data['level'].upper(),
            source_ip=data.get('source_ip'),
            destination_ip=data.get('destination_ip'),
            action=data.get('action'),
            details=json.dumps(data.get('details', {})) if isinstance(data.get('details'), dict) else data.get('details', ''),
            rule_id=data.get('rule_id'),
            user_id=get_jwt_identity()
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Log entry created successfully',
            'log_id': log.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating log: {str(e)}")
        return jsonify({'error': 'Failed to create log entry'}), 500
