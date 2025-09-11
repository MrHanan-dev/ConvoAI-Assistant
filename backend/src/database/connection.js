const knex = require('knex');
const config = require('../config/database');

const db = knex(config[process.env.NODE_ENV || 'development']);

module.exports = db;
