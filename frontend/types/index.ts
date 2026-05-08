export interface Citation {
  id: number;
  text: string;
  metadata: any;
}

export interface Message {
  id: number;
  type: "user" | "ai";
  text: string;
  citations?: Citation[];
}
