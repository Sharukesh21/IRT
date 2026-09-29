export interface EvaluationBenchmark {
    id: string;
    benchmark_id: string;
    scenario_name: string;
    description: string;
    failure_type: string;
    category: string;
    severity: string;
    tags: string[];
}

export interface EvaluationMetrics {
    total_experiments: number;
    detection_rate: number;
    reproduction_rate: number;
    test_generation_rate: number;
    passing_regression_rate: number;
    end_to_end_conversion_rate: number;
    status?: string;
}
