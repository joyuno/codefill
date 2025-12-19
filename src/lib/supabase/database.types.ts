export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string;
          email: string;
          password_hash: string | null;
          name: string | null;
          avatar_url: string | null;
          provider: string;
          provider_id: string | null;
          created_at: string;
          updated_at: string;
          deleted_at: string | null;
        };
        Insert: {
          id?: string;
          email: string;
          password_hash?: string | null;
          name?: string | null;
          avatar_url?: string | null;
          provider?: string;
          provider_id?: string | null;
          created_at?: string;
          updated_at?: string;
          deleted_at?: string | null;
        };
        Update: {
          id?: string;
          email?: string;
          password_hash?: string | null;
          name?: string | null;
          avatar_url?: string | null;
          provider?: string;
          provider_id?: string | null;
          created_at?: string;
          updated_at?: string;
          deleted_at?: string | null;
        };
      };
      user_stats: {
        Row: {
          id: string;
          user_id: string;
          total_xp: number;
          level: number;
          problems_solved: number;
          problems_attempted: number;
          blank_solved: number;
          bug_solved: number;
          output_solved: number;
          refactor_solved: number;
          current_streak: number;
          longest_streak: number;
          last_activity_date: string | null;
          seeds: number;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          total_xp?: number;
          level?: number;
          problems_solved?: number;
          problems_attempted?: number;
          blank_solved?: number;
          bug_solved?: number;
          output_solved?: number;
          refactor_solved?: number;
          current_streak?: number;
          longest_streak?: number;
          last_activity_date?: string | null;
          seeds?: number;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          total_xp?: number;
          level?: number;
          problems_solved?: number;
          problems_attempted?: number;
          blank_solved?: number;
          bug_solved?: number;
          output_solved?: number;
          refactor_solved?: number;
          current_streak?: number;
          longest_streak?: number;
          last_activity_date?: string | null;
          seeds?: number;
          created_at?: string;
          updated_at?: string;
        };
      };
      user_preferences: {
        Row: {
          id: string;
          user_id: string;
          preferred_language: string;
          preferred_difficulty: string;
          daily_goal: number;
          email_notifications: boolean;
          push_notifications: boolean;
          review_reminders: boolean;
          theme: string;
          editor_font_size: number;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          preferred_language?: string;
          preferred_difficulty?: string;
          daily_goal?: number;
          email_notifications?: boolean;
          push_notifications?: boolean;
          review_reminders?: boolean;
          theme?: string;
          editor_font_size?: number;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          preferred_language?: string;
          preferred_difficulty?: string;
          daily_goal?: number;
          email_notifications?: boolean;
          push_notifications?: boolean;
          review_reminders?: boolean;
          theme?: string;
          editor_font_size?: number;
          created_at?: string;
          updated_at?: string;
        };
      };
      codes: {
        Row: {
          id: string;
          framework: string;
          category: string | null;
          tags: string[] | null;
          title: string;
          description: string | null;
          code: string;
          difficulty: string;
          source: string | null;
          source_url: string | null;
          embedding: number[] | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          framework: string;
          category?: string | null;
          tags?: string[] | null;
          title: string;
          description?: string | null;
          code: string;
          difficulty?: string;
          source?: string | null;
          source_url?: string | null;
          embedding?: number[] | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          framework?: string;
          category?: string | null;
          tags?: string[] | null;
          title?: string;
          description?: string | null;
          code?: string;
          difficulty?: string;
          source?: string | null;
          source_url?: string | null;
          embedding?: number[] | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      problems: {
        Row: {
          id: string;
          code_id: string | null;
          problem_type: string;
          problem_code: string;
          answer_data: Json;
          test_cases: Json | null;
          hints: Json | null;
          difficulty: string;
          times_attempted: number;
          times_solved: number;
          avg_solve_time: number | null;
          embedding: number[] | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          code_id?: string | null;
          problem_type: string;
          problem_code: string;
          answer_data: Json;
          test_cases?: Json | null;
          hints?: Json | null;
          difficulty?: string;
          times_attempted?: number;
          times_solved?: number;
          avg_solve_time?: number | null;
          embedding?: number[] | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          code_id?: string | null;
          problem_type?: string;
          problem_code?: string;
          answer_data?: Json;
          test_cases?: Json | null;
          hints?: Json | null;
          difficulty?: string;
          times_attempted?: number;
          times_solved?: number;
          avg_solve_time?: number | null;
          embedding?: number[] | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      attempts: {
        Row: {
          id: string;
          user_id: string;
          problem_id: string;
          is_correct: boolean;
          score: number | null;
          submitted_code: string | null;
          submitted_answer: string | null;
          started_at: string | null;
          submitted_at: string;
          time_spent: number | null;
          hints_used: number;
          xp_earned: number;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          problem_id: string;
          is_correct: boolean;
          score?: number | null;
          submitted_code?: string | null;
          submitted_answer?: string | null;
          started_at?: string | null;
          submitted_at?: string;
          time_spent?: number | null;
          hints_used?: number;
          xp_earned?: number;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          problem_id?: string;
          is_correct?: boolean;
          score?: number | null;
          submitted_code?: string | null;
          submitted_answer?: string | null;
          started_at?: string | null;
          submitted_at?: string;
          time_spent?: number | null;
          hints_used?: number;
          xp_earned?: number;
          created_at?: string;
        };
      };
      attempt_details: {
        Row: {
          id: string;
          attempt_id: string;
          error_type: string | null;
          error_location: number | null;
          error_description: string | null;
          test_results: Json | null;
          review_feedback: Json | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          attempt_id: string;
          error_type?: string | null;
          error_location?: number | null;
          error_description?: string | null;
          test_results?: Json | null;
          review_feedback?: Json | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          attempt_id?: string;
          error_type?: string | null;
          error_location?: number | null;
          error_description?: string | null;
          test_results?: Json | null;
          review_feedback?: Json | null;
          created_at?: string;
        };
      };
      hint_logs: {
        Row: {
          id: string;
          user_id: string;
          problem_id: string;
          attempt_id: string | null;
          hint_level: number;
          hint_content: string | null;
          xp_cost: number;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          problem_id: string;
          attempt_id?: string | null;
          hint_level: number;
          hint_content?: string | null;
          xp_cost?: number;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          problem_id?: string;
          attempt_id?: string | null;
          hint_level?: number;
          hint_content?: string | null;
          xp_cost?: number;
          created_at?: string;
        };
      };
      daily_activity: {
        Row: {
          id: string;
          user_id: string;
          activity_date: string;
          problems_solved: number;
          xp_earned: number;
          time_spent: number;
          blank_count: number;
          bug_count: number;
          output_count: number;
          refactor_count: number;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          activity_date: string;
          problems_solved?: number;
          xp_earned?: number;
          time_spent?: number;
          blank_count?: number;
          bug_count?: number;
          output_count?: number;
          refactor_count?: number;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          activity_date?: string;
          problems_solved?: number;
          xp_earned?: number;
          time_spent?: number;
          blank_count?: number;
          bug_count?: number;
          output_count?: number;
          refactor_count?: number;
          created_at?: string;
          updated_at?: string;
        };
      };
      badges: {
        Row: {
          id: string;
          code: string;
          name: string;
          description: string | null;
          icon_url: string | null;
          condition_type: string;
          condition_value: number | null;
          condition_data: Json | null;
          rarity: string;
          xp_reward: number;
          created_at: string;
        };
        Insert: {
          id?: string;
          code: string;
          name: string;
          description?: string | null;
          icon_url?: string | null;
          condition_type: string;
          condition_value?: number | null;
          condition_data?: Json | null;
          rarity?: string;
          xp_reward?: number;
          created_at?: string;
        };
        Update: {
          id?: string;
          code?: string;
          name?: string;
          description?: string | null;
          icon_url?: string | null;
          condition_type?: string;
          condition_value?: number | null;
          condition_data?: Json | null;
          rarity?: string;
          xp_reward?: number;
          created_at?: string;
        };
      };
      user_badges: {
        Row: {
          id: string;
          user_id: string;
          badge_id: string;
          earned_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          badge_id: string;
          earned_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          badge_id?: string;
          earned_at?: string;
        };
      };
      plans: {
        Row: {
          id: string;
          code: string;
          name: string;
          price_monthly: number;
          price_yearly: number;
          daily_problem_limit: number | null;
          ai_tutor_access: boolean;
          learning_path_access: boolean;
          interview_prep_access: boolean;
          features: Json | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          code: string;
          name: string;
          price_monthly?: number;
          price_yearly?: number;
          daily_problem_limit?: number | null;
          ai_tutor_access?: boolean;
          learning_path_access?: boolean;
          interview_prep_access?: boolean;
          features?: Json | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          code?: string;
          name?: string;
          price_monthly?: number;
          price_yearly?: number;
          daily_problem_limit?: number | null;
          ai_tutor_access?: boolean;
          learning_path_access?: boolean;
          interview_prep_access?: boolean;
          features?: Json | null;
          created_at?: string;
        };
      };
      subscriptions: {
        Row: {
          id: string;
          user_id: string;
          plan_id: string;
          started_at: string;
          expires_at: string | null;
          status: string;
          billing_cycle: string | null;
          next_billing_at: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          plan_id: string;
          started_at?: string;
          expires_at?: string | null;
          status?: string;
          billing_cycle?: string | null;
          next_billing_at?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          plan_id?: string;
          started_at?: string;
          expires_at?: string | null;
          status?: string;
          billing_cycle?: string | null;
          next_billing_at?: string | null;
          created_at?: string;
          updated_at?: string;
        };
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      [_ in never]: never;
    };
    Enums: {
      [_ in never]: never;
    };
  };
};

export type Tables<T extends keyof Database['public']['Tables']> =
  Database['public']['Tables'][T]['Row'];
export type TablesInsert<T extends keyof Database['public']['Tables']> =
  Database['public']['Tables'][T]['Insert'];
export type TablesUpdate<T extends keyof Database['public']['Tables']> =
  Database['public']['Tables'][T]['Update'];
