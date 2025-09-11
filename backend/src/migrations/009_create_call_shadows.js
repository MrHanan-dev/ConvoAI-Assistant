exports.up = function(knex) {
  return knex.schema.createTable('call_shadows', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.uuid('conversation_id').references('id').inTable('conversations').onDelete('CASCADE');
    table.uuid('manager_id').references('id').inTable('users').onDelete('CASCADE');
    table.uuid('rep_id').references('id').inTable('users').onDelete('CASCADE');
    table.json('coaching_notes').defaultTo('[]'); // Real-time coaching comments
    table.json('flagged_moments').defaultTo('[]'); // Important moments flagged by AI
    table.json('performance_tags').defaultTo('[]'); // Performance indicators
    table.json('improvement_areas').defaultTo('[]'); // Areas for improvement
    table.float('overall_score');
    table.json('detailed_scores').defaultTo('{}'); // Breakdown by category
    table.text('summary');
    table.text('action_items');
    table.boolean('is_completed').defaultTo(false);
    table.timestamps(true, true);
    
    // Indexes
    table.index(['conversation_id']);
    table.index(['manager_id']);
    table.index(['rep_id']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('call_shadows');
};
