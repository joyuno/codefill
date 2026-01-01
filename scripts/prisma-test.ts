import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  try {
    // Test connection by counting base_problems
    const count = await prisma.base_problems.count()
    console.log(`Connection successful! Found ${count} base problems.`)

    // Get a sample problem
    const sample = await prisma.base_problems.findFirst({
      select: {
        original_id: true,
        name: true,
        difficulty: true,
        tags: true,
      }
    })
    if (sample) {
      console.log(`Sample problem: ${sample.name} (${sample.difficulty})`)
      console.log(`Tags: ${sample.tags?.join(', ') || 'none'}`)
    }
  } catch (error) {
    console.error('Connection failed:', error)
  } finally {
    await prisma.$disconnect()
  }
}

main()
