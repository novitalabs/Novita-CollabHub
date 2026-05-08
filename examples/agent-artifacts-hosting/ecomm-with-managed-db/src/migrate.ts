import mysql from 'mysql2/promise'
import { readFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'
import 'dotenv/config'

const __dirname = dirname(fileURLToPath(import.meta.url))

function parseDatabaseUrl(url: string): string {
  return url
    .replace('mysql+pymysql://', 'mysql://')
    .replace(/[&?]ssl_verify_cert=[^&]*/g, '')
    .replace(/[&?]ssl_verify_identity=[^&]*/g, '')
}

function splitStatements(sql: string): string[] {
  const noComments = sql
    .split('\n')
    .map(line => {
      const commentIndex = line.indexOf('--')
      if (commentIndex >= 0) {
        return line.substring(0, commentIndex)
      }
      return line
    })
    .join('\n')

  return noComments
    .split(';')
    .map(s => s.trim())
    .filter(s => s.length > 0)
}

async function runMigrations() {
  if (!process.env.DATABASE_URL) {
    console.error('DATABASE_URL environment variable is not set')
    process.exit(1)
  }

  const cleanUrl = parseDatabaseUrl(process.env.DATABASE_URL)
  const connection = await mysql.createConnection({
    uri: cleanUrl,
    ssl: { rejectUnauthorized: true },
    multipleStatements: false,
  })

  console.log('Starting database migrations...\n')

  try {
    const schemaPath = join(__dirname, '..', 'migrations', '0001_initial_schema.sql')
    const schemaSql = readFileSync(schemaPath, 'utf-8')
    const schemaStatements = splitStatements(schemaSql)

    console.log(`Running schema migration (${schemaStatements.length} statements)...`)
    for (let i = 0; i < schemaStatements.length; i++) {
      const stmt = schemaStatements[i]
      console.log(`  [${i + 1}/${schemaStatements.length}] ${stmt.substring(0, 50)}...`)
      await connection.execute(stmt)
    }
    console.log('Schema migration completed\n')

    const seedPath = join(__dirname, '..', 'migrations', '0002_seed_data.sql')
    const seedSql = readFileSync(seedPath, 'utf-8')
    const seedStatements = splitStatements(seedSql)

    console.log(`Running seed data (${seedStatements.length} statements)...`)
    for (let i = 0; i < seedStatements.length; i++) {
      const stmt = seedStatements[i]
      console.log(`  [${i + 1}/${seedStatements.length}] ${stmt.substring(0, 50)}...`)
      await connection.execute(stmt)
    }
    console.log('Seed data completed\n')

    console.log('All database migrations completed!')
  } catch (error) {
    console.error('Migration failed:', error)
    process.exit(1)
  } finally {
    await connection.end()
  }
}

runMigrations()
