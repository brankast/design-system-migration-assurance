export type ChangeType =
  | 'breaking'
  | 'deprecated'
  | 'behavior'
  | 'removed'
  | 'migration';

export type Severity = 'low' | 'medium' | 'high';
export type Confidence = 'documented' | 'inferred' | 'uncertain';

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
