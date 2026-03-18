import { neon, neonConfig, Pool } from '@neondatabase/serverless'
import 'dotenv/config'

// Configure Neon
neonConfig.fetchConnectionCache = true

// Neon serverless SQL function (for simple queries)
const sql = neon(process.env.DATABASE_URL!)

// Create Neon connection pool (for transactions)
export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
})

// Test database connection
console.log('✅ Neon serverless database configured')

// Export query helper function
export const query = async (text: string, params?: unknown[]) => {
  const start = Date.now()
  const result = await sql(text, params as any)
  const duration = Date.now() - start
  if (process.env.NODE_ENV === 'development') {
    console.log('Query executed:', { text, duration: `${duration}ms`, rows: result.length })
  }
  // Return pg-compatible result format
  return { rows: result, rowCount: result.length }
}

