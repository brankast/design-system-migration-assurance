export type ChangeType =
  | 'breaking'
  | 'deprecated'
  | 'behavior'
  | 'removed'
  | 'migration';

export type Severity = 'low' | 'medium' | 'high';
export type Confidence = 'documented' | 'inferred' | 'uncertain';
export type UsageType = 'component' | 'property' | 'directive' | 'token';
export type Risk = 'none' | 'low' | 'medium' | 'high';
export type Action = 'none' | 'review' | 'patch';

export interface ChangeEvent {
  id: string;
  library: string;
  fromVersion: string;
  toVersion: string;
  component: string;
  changeType: ChangeType;
  severity: Severity;
  description: string;
  affectedApi?: string;
  migrationPath?: string;
  sourceUrl?: string;
  evidence?: string;
  replacement?: string;
  packageName?: string;
  confidence?: Confidence;
}

export interface ComponentUsage {
  project: string;
  component: string;
  usageType: UsageType;
  file: string;
  line: number;
  matchedApi?: string;
  codeSnippet?: string;
}

export interface Impact {
  changeId: string;
  risk: Risk;
  action: Action;
  usages: ComponentUsage[];
  uncertainty?: string | null;
}

export interface ProposedPatch {
  file: string;
  description: string;
  find: string;
  replace: string;
  sourceEvidence: string;
  applied: boolean;
}

export interface Assessment {
  library: string;
  installedVersion: string;
  latestVersion: string;
  fromVersion: string;
  toVersion: string;
  changelogSource: string;
  changeEvents: ChangeEvent[];
  usages: ComponentUsage[];
  impacts: Impact[];
  patches: ProposedPatch[];
  summary: string;
  prRequired: boolean;
}
