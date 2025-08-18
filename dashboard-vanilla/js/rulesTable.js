async function fetchRules() {
  try {
    const res = await fetch('http://localhost:5000/rules/');
    const rules = await res.json();
    renderRulesTable(rules);
  } catch (err) {
    console.error('Error fetching rules:', err);
    document.getElementById('rules-container').innerText = 'Failed to load rules.';
  }
}

function renderRulesTable(rules) {
  const container = document.getElementById('rules-container');
  container.innerHTML = '';

  if (!rules.length) {
    container.innerText = 'No rules found.';
    return;
  }

  const table = document.createElement('table');
  table.innerHTML = `
    <thead>
      <tr>
        <th>ID</th>
        <th>Source</th>
        <th>Destination</th>
        <th>Action</th>
        <th>Delete</th>
      </tr>
    </thead>
    <tbody>
      ${rules.map(r => `<tr>
        <td>${r.id}</td>
        <td>${r.source}</td>
        <td>${r.destination}</td>
        <td>${r.action}</td>
        <td><button onclick="deleteRule(${r.id})">Delete</button></td>
      </tr>`).join('')}
    </tbody>
  `;
  container.appendChild(table);
}

// Add a new rule
async function addRule() {
  const source = document.getElementById('rule-source').value;
  const destination = document.getElementById('rule-destination').value;
  const action = document.getElementById('rule-action').value;

  if (!source || !destination) {
    alert('Please fill in both Source and Destination fields.');
    return;
  }

  try {
    const res = await fetch('http://localhost:5000/rules', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({source, destination, action})
    });

    if (res.ok) {
      fetchRules(); // refresh table
      document.getElementById('rule-source').value = '';
      document.getElementById('rule-destination').value = '';
    } else {
      alert('Failed to add rule.');
    }
  } catch (err) {
    console.error('Error adding rule:', err);
  }
}

// Delete a rule by ID
async function deleteRule(id) {
  if (!confirm('Are you sure you want to delete this rule?')) return;

  try {
    const res = await fetch(`http://localhost:5000/rules/${id}`, { method: 'DELETE' });
    if (res.ok) {
      fetchRules(); // refresh table
    } else {
      alert('Failed to delete rule.');
    }
  } catch (err) {
    console.error('Error deleting rule:', err);
  }
}
