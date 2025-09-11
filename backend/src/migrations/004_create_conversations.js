exports.up = function(knex) {
  return knex.schema.createTable('conversations', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.uuid('user_id').references('id').inTable('users').onDelete('CASCADE');
    table.uuid('team_id').references('id').inTable('teams').onDelete('SET NULL');
    table.string('title');
    table.enum('type', ['sales_call', 'interview', 'meeting', 'support', 'other']).defaultTo('meeting');
    table.enum('platform', ['zoom', 'teams', 'google_meet', 'other']).defaultTo('other');
    table.timestamp('started_at');
    table.timestamp('ended_at');
    table.integer('duration_seconds');
    table.json('participants').defaultTo('[]');
    table.text('transcript');
    table.json('ai_suggestions').defaultTo('[]');
    table.json('objections_handled').defaultTo('[]');
    table.json('analytics').defaultTo('{}');
    table.json('metadata').defaultTo('{}');
    table.float('sentiment_score');
    table.float('engagement_score');
    table.float('clarity_score');
    table.float('conviction_score');
    table.enum('outcome', ['won', 'lost', 'follow_up', 'pending']).defaultTo('pending');
    table.text('summary');
    table.text('action_items');
    table.boolean('is_processed').defaultTo(false);
    table.timestamps(true, true);
    
    // Indexes
    table.index(['user_id']);
    table.index(['team_id']);
    table.index(['started_at']);
    table.index(['type']);
    table.index(['platform']);
    table.index(['outcome']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('conversations');
};
