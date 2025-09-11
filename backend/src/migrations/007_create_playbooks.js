exports.up = function(knex) {
  return knex.schema.createTable('playbooks', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.uuid('user_id').references('id').inTable('users').onDelete('CASCADE');
    table.uuid('team_id').references('id').inTable('teams').onDelete('CASCADE');
    table.string('name').notNullable();
    table.text('description');
    table.enum('type', ['sales', 'support', 'interview', 'demo', 'other']).defaultTo('sales');
    table.json('talk_tracks').defaultTo('[]'); // Structured conversation flows
    table.json('message_frameworks').defaultTo('[]'); // Key messaging points
    table.json('question_sequences').defaultTo('[]'); // Discovery questions
    table.json('closing_techniques').defaultTo('[]'); // Closing strategies
    table.json('objection_handling').defaultTo('[]'); // Linked objection templates
    table.json('success_criteria').defaultTo('{}'); // KPIs and goals
    table.integer('usage_count').defaultTo(0);
    table.float('success_rate').defaultTo(0);
    table.boolean('is_active').defaultTo(true);
    table.timestamps(true, true);
    
    // Indexes
    table.index(['user_id']);
    table.index(['team_id']);
    table.index(['type']);
    table.index(['is_active']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('playbooks');
};
