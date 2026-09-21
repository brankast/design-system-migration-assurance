export type UsageType =
  | 'component'
  | 'property'
  | 'directive'
  | 'token';

export interface ComponentUsage {
  project: string;

  component: string;
  usageType: UsageType;

  file: string;
  line: number;

  matchedApi?: string;
  codeSnippet?: string;
}