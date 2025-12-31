/**
 * API Route: Generated Problem Management
 *
 * POST /api/problems/generated - Save a generated problem (blank/puzzle/guided)
 */

import { NextRequest, NextResponse } from 'next/server';
import prisma from '@/lib/prisma';
import type { Prisma } from '@prisma/client';

// Type definitions
interface BlankProblemInput {
  type: 'blank';
  original_id: string;
  language: string;
  code_template: string;
  answers: string[];
  creator_id?: string;
}

interface PuzzleProblemInput {
  type: 'puzzle';
  original_id: string;
  language: string;
  fixed_start?: string;
  fixed_end?: string;
  blocks: Array<{ id: number; code: string }>;
  creator_id?: string;
}

interface GuidedProblemInput {
  type: 'guided';
  original_id: string;
  language: string;
  concepts: string[];
  flow: string[];
  checkpoints: string[];
  creator_id?: string;
}

type GeneratedProblemInput = BlankProblemInput | PuzzleProblemInput | GuidedProblemInput;

/**
 * POST /api/problems/generated
 * Save a generated problem (blank, puzzle, or guided)
 */
export async function POST(request: NextRequest) {
  try {
    const body: GeneratedProblemInput = await request.json();

    // Validate required fields
    if (!body.type || !body.original_id || !body.language) {
      return NextResponse.json(
        { error: 'Missing required fields: type, original_id, language' },
        { status: 400 }
      );
    }

    // Get base_problem_id from original_id
    const baseProblem = await prisma.base_problems.findUnique({
      where: { original_id: body.original_id },
      select: { id: true },
    });

    const baseProblemId = baseProblem?.id || null;

    let result;

    switch (body.type) {
      case 'blank': {
        const blankBody = body as BlankProblemInput;

        // Check for existing
        const existingBlank = await prisma.problems_blank.findFirst({
          where: {
            original_id: blankBody.original_id,
            language: blankBody.language,
          },
        });

        if (existingBlank) {
          return NextResponse.json({
            success: true,
            id: existingBlank.id,
            cached: true,
          });
        }

        result = await prisma.problems_blank.create({
          data: {
            original_id: blankBody.original_id,
            base_problem_id: baseProblemId,
            language: blankBody.language,
            code_template: blankBody.code_template,
            answers: blankBody.answers,
            creator_id: blankBody.creator_id || null,
          },
        });
        break;
      }

      case 'puzzle': {
        const puzzleBody = body as PuzzleProblemInput;

        // Check for existing
        const existingPuzzle = await prisma.problems_puzzle.findFirst({
          where: {
            original_id: puzzleBody.original_id,
            language: puzzleBody.language,
          },
        });

        if (existingPuzzle) {
          return NextResponse.json({
            success: true,
            id: existingPuzzle.id,
            cached: true,
          });
        }

        result = await prisma.problems_puzzle.create({
          data: {
            original_id: puzzleBody.original_id,
            base_problem_id: baseProblemId,
            language: puzzleBody.language,
            fixed_start: puzzleBody.fixed_start || null,
            fixed_end: puzzleBody.fixed_end || null,
            blocks: puzzleBody.blocks as Prisma.InputJsonValue,
            creator_id: puzzleBody.creator_id || null,
          },
        });
        break;
      }

      case 'guided': {
        const guidedBody = body as GuidedProblemInput;

        // Check for existing
        const existingGuided = await prisma.problems_guided.findFirst({
          where: {
            original_id: guidedBody.original_id,
            language: guidedBody.language,
          },
        });

        if (existingGuided) {
          return NextResponse.json({
            success: true,
            id: existingGuided.id,
            cached: true,
          });
        }

        result = await prisma.problems_guided.create({
          data: {
            original_id: guidedBody.original_id,
            base_problem_id: baseProblemId,
            language: guidedBody.language,
            concepts: guidedBody.concepts,
            flow: guidedBody.flow,
            checkpoints: guidedBody.checkpoints,
            creator_id: guidedBody.creator_id || null,
          },
        });
        break;
      }

      default:
        return NextResponse.json(
          { error: 'Invalid problem type. Must be blank, puzzle, or guided' },
          { status: 400 }
        );
    }

    return NextResponse.json({
      success: true,
      id: result.id,
      type: body.type,
    });
  } catch (error) {
    console.error('[API/problems/generated] Error saving problem:', error);
    return NextResponse.json(
      { error: 'Failed to save problem', details: String(error) },
      { status: 500 }
    );
  }
}
