exports.up = function(knex) {
  return knex.schema.createTable('objection_templates', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.uuid('user_id').references('id').inTable('users').onDelete('CASCADE');
    table.uuid('team_id').references('id').inTable('teams').onDelete('CASCADE');
    table.string('name').notNullable();
    table.text('description');
    table.string('category'); // price, competition, timing, authority, etc.
    table.json('trigger_phrases').defaultTo('[]'); // Keywords that trigger this objection
    table.text('objection_text');
    table.text('response_template');
    table.json('alternative_responses').defaultTo('[]');
    table.json('battlecard_data').defaultTo('{}'); // Competitive information
    table.integer('usage_count').defaultTo(0);
    table.float('success_rate').defaultTo(0);
    table.boolean('is_active').defaultTo(true);
    table.timestamps(true, true);
    
    // Indexes
    table.index(['user_id']);
    table.index(['team_id']);
    table.index(['category']);
    table.index(['is_active']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('objection_templates');
};
