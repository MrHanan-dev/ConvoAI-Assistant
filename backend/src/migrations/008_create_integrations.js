exports.up = function(knex) {
  return knex.schema.createTable('integrations', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.uuid('user_id').references('id').inTable('users').onDelete('CASCADE');
    table.uuid('team_id').references('id').inTable('teams').onDelete('CASCADE');
    table.enum('provider', ['salesforce', 'hubspot', 'zoom', 'teams', 'google_meet', 'slack', 'other']).notNullable();
    table.string('external_id'); // ID in the external system
    table.json('credentials'); // Encrypted credentials
    table.json('settings').defaultTo('{}'); // Integration-specific settings
    table.json('sync_status').defaultTo('{}'); // Last sync information
    table.boolean('is_active').defaultTo(true);
    table.timestamp('last_sync_at');
    table.timestamps(true, true);
    
    // Indexes
    table.index(['user_id']);
    table.index(['team_id']);
    table.index(['provider']);
    table.index(['is_active']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('integrations');
};
