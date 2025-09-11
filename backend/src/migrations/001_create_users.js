exports.up = function(knex) {
  return knex.schema.createTable('users', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.string('email').unique().notNullable();
    table.string('password_hash').notNullable();
    table.string('first_name').notNullable();
    table.string('last_name').notNullable();
    table.string('company_name');
    table.string('job_title');
    table.string('phone');
    table.enum('plan', ['starter', 'pro', 'enterprise']).defaultTo('starter');
    table.enum('role', ['user', 'manager', 'admin']).defaultTo('user');
    table.json('preferences').defaultTo('{}');
    table.json('integrations').defaultTo('{}');
    table.boolean('email_verified').defaultTo(false);
    table.boolean('is_active').defaultTo(true);
    table.timestamp('last_login');
    table.timestamps(true, true);
    
    // Indexes
    table.index(['email']);
    table.index(['plan']);
    table.index(['is_active']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('users');
};
