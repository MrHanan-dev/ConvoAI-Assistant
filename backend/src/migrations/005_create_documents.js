exports.up = function(knex) {
  return knex.schema.createTable('documents', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.uuid('user_id').references('id').inTable('users').onDelete('CASCADE');
    table.uuid('team_id').references('id').inTable('teams').onDelete('CASCADE');
    table.string('name').notNullable();
    table.text('description');
    table.enum('type', ['sales_deck', 'product_sheet', 'whitepaper', 'faq', 'battlecard', 'other']).defaultTo('other');
    table.string('file_path');
    table.string('file_url');
    table.string('mime_type');
    table.integer('file_size');
    table.text('content'); // Extracted text content
    table.json('embeddings'); // Vector embeddings for similarity search
    table.json('tags').defaultTo('[]');
    table.json('metadata').defaultTo('{}');
    table.boolean('is_active').defaultTo(true);
    table.boolean('is_processed').defaultTo(false);
    table.timestamps(true, true);
    
    // Indexes
    table.index(['user_id']);
    table.index(['team_id']);
    table.index(['type']);
    table.index(['is_active']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('documents');
};
