/**
 * API Route: Problem Management
 *
 * POST /api/problems - Save a new base problem to the database
 * GET /api/problems?original_id=xxx - Get a problem with tags and input_output
 */

import { NextRequest, NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import type { Prisma } from '@prisma/client';

// Type definitions
interface BaseProblemInput {
  original_id: string;
  name: string;
  question: string;
  input_output?: {
    inputs: string[];
    outputs: string[];
  } | null;
  difficulty?: string;
  tags?: string[];
  source?: string;
  url?: string;
  time_limit?: string;
  memory_limit?: string;
  solutions: Array<{
    language: string;
    code: string;
  }>;
  images?: Array<Record<string, unknown>>;
  starter_code?: string;
  explanation?: string;
}

/**
 * POST /api/problems
 * Save a new base problem (e.g., from CodeGen)
 */
export async function POST(request: NextRequest) {
  try {
    const body: BaseProblemInput = await request.json();

    // Validate required fields
    if (!body.original_id || !body.name || !body.question || !body.solutions) {
      return NextResponse.json(
        { error: 'Missing required fields: original_id, name, question, solutions' },
        { status: 400 }
      );
    }

    // Check if problem already exists
    const existing = await prisma.base_problems.findUnique({
      where: { original_id: body.original_id },
    });

    if (existing) {
      return NextResponse.json(
        { error: 'Problem with this original_id already exists', id: existing.id },
        { status: 409 }
      );
    }

    // Create new problem
    const problem = await prisma.base_problems.create({
      data: {
        original_id: body.original_id,
        name: body.name,
        question: body.question,
        input_output: (body.input_output || null) as Prisma.InputJsonValue | null,
        difficulty: body.difficulty || 'medium',
        tags: body.tags || [],
        source: body.source || 'codegen',
        url: body.url,
        time_limit: body.time_limit,
        memory_limit: body.memory_limit,
        solutions: body.solutions as Prisma.InputJsonValue,
        images: (body.images || []) as Prisma.InputJsonValue,
        starter_code: body.starter_code,
        explanation: body.explanation,
      },
    });

    return NextResponse.json({
      success: true,
      id: problem.id,
      original_id: problem.original_id,
    });
  } catch (error) {
    console.error('[API/problems] Error saving problem:', error);
    return NextResponse.json(
      { error: 'Failed to save problem', details: String(error) },
      { status: 500 }
    );
  }
}

/**
 * GET /api/problems?original_id=xxx
 * Get a problem with full details including tags and input_output
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const originalId = searchParams.get('original_id');

    if (!originalId) {
      return NextResponse.json(
        { error: 'Missing original_id query parameter' },
        { status: 400 }
      );
    }

    const problem = await prisma.base_problems.findUnique({
      where: { original_id: originalId },
      select: {
        id: true,
        original_id: true,
        name: true,
        question: true,
        input_output: true,
        difficulty: true,
        tags: true,
        source: true,
        url: true,
        time_limit: true,
        memory_limit: true,
        solutions: true,
        created_at: true,
      },
    });

    if (!problem) {
      return NextResponse.json(
        { error: 'Problem not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(problem);
  } catch (error) {
    console.error('[API/problems] Error fetching problem:', error);
    return NextResponse.json(
      { error: 'Failed to fetch problem', details: String(error) },
      { status: 500 }
    );
  }
}
