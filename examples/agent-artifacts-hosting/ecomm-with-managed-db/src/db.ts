import mysql from 'mysql2/promise'
import 'dotenv/config'

function parseDatabaseUrl(url: string): string {
  return url
    .replace('mysql+pymysql://', 'mysql://')
    .replace(/[&?]ssl_verify_cert=[^&]*/g, '')
    .replace(/[&?]ssl_verify_identity=[^&]*/g, '')
}

if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL environment variable is not set')
}

const cleanUrl = parseDatabaseUrl(process.env.DATABASE_URL)

export const pool = mysql.createPool({
  uri: cleanUrl,
  connectionLimit: 10,
  ssl: { rejectUnauthorized: true },
})

console.log('Managed database configured')

export const query = async (text: string, params?: any[]) => {
  const start = Date.now()
  const [rows] = await pool.execute(text, params)
  const duration = Date.now() - start
  if (process.env.NODE_ENV === 'development') {
    console.log('Query executed:', { text, duration: `${duration}ms` })
  }
  const resultRows = Array.isArray(rows) ? rows : []
  return { rows: resultRows as Record<string, any>[], rowCount: resultRows.length }
}

export const insert = async (text: string, params?: any[]) => {
  const [result] = await pool.execute(text, params) as any
  return { insertId: result.insertId, affectedRows: result.affectedRows }
}
