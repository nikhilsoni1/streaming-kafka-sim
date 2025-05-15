import { DatabaseAPI } from "../data-sources/DatabaseApi";

//This interface is used with graphql-codegen to generate types for resolvers context
export interface DataSourceContext {
  // auth?: string;
  database: DatabaseAPI;
}
