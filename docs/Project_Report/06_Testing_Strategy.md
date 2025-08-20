# Testing Strategy

## Table of Contents
1. [Testing Approach](#1-testing-approach)
2. [Test Environment](#2-test-environment)
3. [Unit Testing](#3-unit-testing)
4. [Integration Testing](#4-integration-testing)
5. [Performance Testing](#5-performance-testing)
6. [Security Testing](#6-security-testing)
7. [End-to-End Testing](#7-end-to-end-testing)
8. [Test Automation](#8-test-automation)
9. [Test Data Management](#9-test-data-management)
10. [Reporting & Metrics](#10-reporting--metrics)

## 1. Testing Approach

### 1.1 Testing Pyramid
```mermaid
graph TD
    A[E2E Tests] -->|10%| B[Integration Tests]
    B -->|20%| C[Unit Tests]
    C -->|70%| D[Code Coverage]
    
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#8f8,stroke:#333
    style D fill:#8f8,stroke:#333
```

### 1.2 Test Types
| Test Type | Tools | Frequency | Owner |
|-----------|-------|-----------|-------|
| Unit Tests | Go test, pytest | On Commit | Developers |
| Integration | TestContainers, pytest | On PR | QA Engineers |
| E2E | Cypress, Selenium | Nightly | QA Team |
| Performance | k6, Locust | Weekly | DevOps |
| Security | OWASP ZAP, Trivy | Weekly | Security Team |
| Load Testing | k6, JMeter | Bi-weekly | DevOps |
| Chaos Testing | Chaos Monkey | Monthly | SRE |

## 2. Test Environment

### 2.1 Environment Matrix
| Environment | Purpose | Data | Access |
|-------------|---------|------|--------|
| Development | Feature development | Mock data | Developers |
| Staging | Integration testing | Anonymized production data | QA Team |
| UAT | User acceptance | Production-like data | Business |
| Production | Live environment | Real production data | Operations |

### 2.2 Test Containers
```yaml
# docker-compose.test.yml
version: '3.8'

services:
  test:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://test:test@postgres:5432/test
      - REDIS_URL=redis://redis:6379/0
    command: >
      sh -c "pytest tests/"

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
      - POSTGRES_DB=test
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test -d test"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
```

## 3. Unit Testing

### 3.1 Go Unit Tests
```go
// policy_engine_test.go
package policy

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestPolicyEvaluation(t *testing.T) {
    tests := []struct {
        name     string
        policy   Policy
        request  Request
        expected bool
    }{
        {
            name: "allow admin access",
            policy: Policy{
                ID:       "p1",
                Effect:   "allow",
                Actions:  []string{"read", "write"},
                Subjects: []string{"user:admin"},
            },
            request: Request{
                Subject: "user:admin",
                Action:  "read",
            },
            expected: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := tt.policy.Evaluate(tt.request)
            assert.Equal(t, tt.expected, result)
        })
    }
}
```

### 3.2 Python Unit Tests
```python
# test_packet_processor.py
import pytest
from unittest.mock import Mock, patch
from firewall.processor import PacketProcessor

def test_process_packet():
    # Setup
    config = {"max_packets": 1000, "timeout": 5}
    processor = PacketProcessor(config)
    mock_packet = Mock()
    
    # Mock dependencies
    with patch('firewall.processor.ProtocolAnalyzer') as mock_analyzer:
        mock_analyzer.analyze.return_value = ("http", {})
        
        # Execute
        result = processor.process_packet(mock_packet)
        
        # Verify
        assert result.processed is True
        mock_analyzer.analyze.assert_called_once_with(mock_packet)
```

## 4. Integration Testing

### 4.1 API Testing
```python
# test_api_integration.py
import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def test_create_policy(api_client, test_policy):
    response = api_client.post(
        "https://api.firewall.example.com/v1/policies",
        json=test_policy,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 201
    assert "id" in response.json()
    return response.json()["id"]

@pytest.mark.dependency(depends=["test_create_policy"])
def test_get_policy(api_client, policy_id):
    response = api_client.get(
        f"https://api.firewall.example.com/v1/policies/{policy_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == policy_id
```

## 5. Performance Testing

### 5.1 k6 Load Test
```javascript
// load_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '5m', target: 100 },  // Ramp up to 100 users
    { duration: '10m', target: 100 }, // Stay at 100 users
    { duration: '5m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests should be below 500ms
    errors: ['rate<0.1'],             // <10% errors
  },
};

export default function () {
  const url = 'https://api.firewall.example.com/v1/policies';
  const params = {
    headers: {
      'Authorization': `Bearer ${__ENV.API_TOKEN}`,
      'Content-Type': 'application/json',
    },
  };

  const payload = JSON.stringify({
    name: 'Test Policy',
    action: 'allow',
    priority: 1,
    conditions: [
      { field: 'source_ip', operator: 'equals', value: '192.168.1.1' }
    ]
  });

  const res = http.post(url, payload, params);
  
  const checkRes = check(res, {
    'status is 201': (r) => r.status === 201,
  });
  
  if (!checkRes) {
    errorRate.add(1);
  }

  sleep(1);
}
```

## 6. Security Testing

### 6.1 OWASP ZAP Scan
```bash
# Run ZAP baseline scan
docker run -v $(pwd):/zap/wrk/:rw \
  -t owasp/zap2docker-stable zap-baseline.py \
  -t https://firewall.example.com \
  -r testreport.html \
  -x report_xml.xml

# Check for vulnerabilities
if grep -q "High" testreport.html; then
  echo "High severity vulnerabilities found!"
  exit 1
fi
```

## 7. End-to-End Testing

### 7.1 Cypress Test
```javascript
// cypress/e2e/policy_management.cy.js
describe('Policy Management', () => {
  beforeEach(() => {
    cy.login('admin@example.com', 'password123');
    cy.visit('/policies');
  });

  it('should create a new policy', () => {
    cy.get('[data-testid="new-policy-button"]').click();
    
    // Fill in the form
    cy.get('[name="name"]').type('Block Social Media');
    cy.get('[name="action"]').select('deny');
    
    // Add condition
    cy.get('[data-testid="add-condition"]').click();
    cy.get('[name="conditions.0.field"]').select('domain');
    cy.get('[name="conditions.0.operator"]').select('contains');
    cy.get('[name="conditions.0.value"]').type('facebook.com');
    
    // Submit form
    cy.get('[type="submit"]').click();
    
    // Verify success
    cy.contains('Policy created successfully');
    cy.url().should('include', '/policies/');
    
    // Verify policy is applied
    cy.visit('/monitor');
    cy.contains('Block Social Media').should('be.visible');
  });
});
```

## 8. Test Automation

### 8.1 GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Go
      uses: actions/setup-go@v3
      with:
        go-version: '1.21'
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: |
        go test -v -coverprofile=coverage.out ./...
        go tool cover -func=coverage.out
    
    - name: Run integration tests
      run: |
        pytest tests/integration -v
    
    - name: Run security scan
      run: |
        docker run --rm \
          -v $(pwd):/zap/wrk/:rw \
          -t owasp/zap2docker-stable zap-baseline.py \
          -t http://localhost:8000 \
          -r zap-report.html \
          -x report_xml.xml
```

## 9. Test Data Management

### 9.1 Factory Boy Factories
```python
# tests/factories.py
import factory
from factory.django import DjangoModelFactory
from firewall.models import Policy, Rule, Condition

class ConditionFactory(DjangoModelFactory):
    class Meta:
        model = Condition
    
    field = 'source_ip'
    operator = 'equals'
    value = factory.Faker('ipv4')

class PolicyFactory(DjangoModelFactory):
    class Meta:
        model = Policy
    
    name = factory.Faker('sentence', nb_words=3)
    action = 'allow'
    priority = factory.Sequence(int)
    
    @factory.post_generation
    def rules(self, create, extracted, **kwargs):
        if not create:
            return
            
        if extracted:
            for rule in extracted:
                self.rules.add(rule)
        else:
            self.rules.add(RuleFactory())
```

## 10. Reporting & Metrics

### 10.1 Test Coverage Report
```bash
# Generate coverage report
pytest --cov=firewall --cov-report=html tests/

# View coverage in browser
python -m http.server 8000 --directory htmlcov/
```

### 10.2 Test Metrics
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Unit Test Coverage | 90% | 87% | ⚠️ |
| Integration Test Coverage | 80% | 82% | ✅ |
| Test Execution Time | < 5 min | 3m 42s | ✅ |
| Flaky Tests | 0 | 2 | ❌ |
| Critical Bugs | 0 | 0 | ✅ |
| High Severity Bugs | 0 | 0 | ✅ |
| Medium Severity Bugs | < 5 | 3 | ✅ |
| Open Security Issues | 0 | 1 | ⚠️ |

---
*Document Version: 1.0.0*  
*Last Updated: August 20, 2025*
