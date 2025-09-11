exports.up = function(knex) {
  return knex.schema.createTable('team_members', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.uuid('team_id').references('id').inTable('teams').onDelete('CASCADE');
    table.uuid('user_id').references('id').inTable('users').onDelete('CASCADE');
    table.enum('role', ['member', 'manager', 'admin']).defaultTo('member');
    table.json('permissions').defaultTo('{}');
    table.timestamp('joined_at').defaultTo(knex.fn.now());
    table.timestamps(true, true);
    
    // Unique constraint
    table.unique(['team_id', 'user_id']);
    
    // Indexes
    table.index(['team_id']);
    table.index(['user_id']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('team_members');
};
