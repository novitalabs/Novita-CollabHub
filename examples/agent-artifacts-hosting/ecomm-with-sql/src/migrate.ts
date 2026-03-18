import { neon } from '@neondatabase/serverless'
import { readFileSync } from 'fs'
import { join } from 'path'
import 'dotenv/config'

// Split SQL statements: remove comments, then split by semicolons
function splitStatements(sql: string): string[] {
  // Remove single-line comments
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
  
  // Split by semicolons, filter empty statements
  return noComments
    .split(';')
    .map(s => s.trim())
    .filter(s => s.length > 0)
}

async function runMigrations() {
  if (!process.env.DATABASE_URL) {
    console.error('❌ DATABASE_URL environment variable is not set')
    process.exit(1)
  }

  const sql = neon(process.env.DATABASE_URL)
  
  console.log('🚀 Starting database migrations...\n')

  try {
    // Read and execute schema migration
    const schemaPath = join(import.meta.dirname, '..', 'migrations', '0001_initial_schema.sql')
    const schemaSql = readFileSync(schemaPath, 'utf-8')
    const schemaStatements = splitStatements(schemaSql)
    
    console.log(`📦 Running schema migration (${schemaStatements.length} statements)...`)
    for (let i = 0; i < schemaStatements.length; i++) {
      const stmt = schemaStatements[i]
      console.log(`  [${i + 1}/${schemaStatements.length}] ${stmt.substring(0, 50)}...`)
      await sql(stmt)
    }
    console.log('✅ Schema migration completed\n')

    // Read and execute seed data
    const seedPath = join(import.meta.dirname, '..', 'migrations', '0002_seed_data.sql')
    const seedSql = readFileSync(seedPath, 'utf-8')
    const seedStatements = splitStatements(seedSql)
    
    console.log(`🌱 Running seed data (${seedStatements.length} statements)...`)
    for (let i = 0; i < seedStatements.length; i++) {
      const stmt = seedStatements[i]
      console.log(`  [${i + 1}/${seedStatements.length}] ${stmt.substring(0, 50)}...`)
      await sql(stmt)
    }
    console.log('✅ Seed data completed\n')

    console.log('🎉 All database migrations completed!')
  } catch (error) {
    console.error('❌ Migration failed:', error)
    process.exit(1)
  }
}

runMigrations()
