from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.models.db import db, Rule, User
from server.services.security_service import admin_required, log_activity
import json

rules_bp = Blueprint('rules', __name__)

@rules_bp.route('', methods=['GET'])
@jwt_required()
def get_rules():
    """
    Get all firewall rules
    ---
    tags:
      - Rules
    security:
      - JWT: []
    responses:
      200:
        description: List of all rules
        schema:
          type: array
          items:
            $ref: '#/definitions/Rule'
    """
    try:
        rules = Rule.query.all()
        return jsonify([{
            'id': rule.id,
            'name': rule.name,
            'description': rule.description,
            'source_ip': rule.source_ip,
            'source_port': rule.source_port,
            'destination_ip': rule.destination_ip,
            'destination_port': rule.destination_port,
            'protocol': rule.protocol,
            'action': rule.action,
            'is_active': rule.is_active,
            'created_at': rule.created_at.isoformat() if rule.created_at else None,
            'updated_at': rule.updated_at.isoformat() if rule.updated_at else None
        } for rule in rules]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rules_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_rule():
    """
    Create a new firewall rule
    ---
    tags:
      - Rules
    security:
      - JWT: []
    parameters:
      - in: body
        name: rule
        description: The rule to create
        schema:
          $ref: '#/definitions/Rule'
    responses:
      201:
        description: Rule created successfully
      400:
        description: Invalid input
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'action']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new rule
        rule = Rule(
            name=data['name'],
            description=data.get('description', ''),
            source_ip=data.get('source_ip'),
            source_port=data.get('source_port'),
            destination_ip=data.get('destination_ip'),
            destination_port=data.get('destination_port'),
            protocol=data.get('protocol', 'any'),
            action=data['action'].upper(),
            is_active=data.get('is_active', True),
            created_by=get_jwt_identity()
        )
        
        db.session.add(rule)
        db.session.commit()
        
        # Log the action
        log_activity(
            event_type="RULES",
            user_id=get_jwt_identity(),
            details={
                "action": "create_rule",
                "rule_id": rule.id,
                "rule_name": rule.name
            }
        )
        
        return jsonify({
            'message': 'Rule created successfully',
            'rule_id': rule.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rules_bp.route('/<int:rule_id>', methods=['GET'])
@jwt_required()
def get_rule(rule_id):
    """
    Get a specific rule by ID
    ---
    tags:
      - Rules
    security:
      - JWT: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
        description: ID of the rule to get
    responses:
      200:
        description: Rule details
        schema:
          $ref: '#/definitions/Rule'
      404:
        description: Rule not found
    """
    rule = Rule.query.get_or_404(rule_id)
    return jsonify({
        'id': rule.id,
        'name': rule.name,
        'description': rule.description,
        'source_ip': rule.source_ip,
        'source_port': rule.source_port,
        'destination_ip': rule.destination_ip,
        'destination_port': rule.destination_port,
        'protocol': rule.protocol,
        'action': rule.action,
        'is_active': rule.is_active,
        'created_at': rule.created_at.isoformat() if rule.created_at else None,
        'updated_at': rule.updated_at.isoformat() if rule.updated_at else None
    })

@rules_bp.route('/<int:rule_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_rule(rule_id):
    """
    Update an existing rule
    ---
    tags:
      - Rules
    security:
      - JWT: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
        description: ID of the rule to update
      - in: body
        name: rule
        description: Updated rule data
        schema:
          $ref: '#/definitions/Rule'
    responses:
      200:
        description: Rule updated successfully
      404:
        description: Rule not found
    """
    try:
        rule = Rule.query.get_or_404(rule_id)
        data = request.get_json()
        
        # Update fields if provided
        updatable_fields = [
            'name', 'description', 'source_ip', 'source_port',
            'destination_ip', 'destination_port', 'protocol', 'action', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(rule, field, data[field])
        
        db.session.commit()
        
        # Log the action
        log_activity(
            event_type="RULES",
            user_id=get_jwt_identity(),
            details={
                "action": "update_rule",
                "rule_id": rule.id,
                "rule_name": rule.name,
                "changes": data
            }
        )
        
        return jsonify({'message': 'Rule updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@rules_bp.route('/<int:rule_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_rule(rule_id):
    """
    Delete a rule
    ---
    tags:
      - Rules
    security:
      - JWT: []
    parameters:
      - name: rule_id
        in: path
        type: integer
        required: true
        description: ID of the rule to delete
    responses:
      200:
        description: Rule deleted successfully
      404:
        description: Rule not found
    """
    try:
        rule = Rule.query.get_or_404(rule_id)
        
        # Log the action before deletion
        log_activity(
            event_type="RULES",
            user_id=get_jwt_identity(),
            details={
                "action": "delete_rule",
                "rule_id": rule.id,
                "rule_name": rule.name
            }
        )
        
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({'message': 'Rule deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
