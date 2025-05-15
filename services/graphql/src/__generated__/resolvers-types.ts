import { GraphQLResolveInfo } from 'graphql';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
export type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
export type MakeOptional<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]?: Maybe<T[SubKey]> };
export type MakeMaybe<T, K extends keyof T> = Omit<T, K> & { [SubKey in K]: Maybe<T[SubKey]> };
export type MakeEmpty<T extends { [key: string]: unknown }, K extends keyof T> = { [_ in K]?: never };
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
export type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
export type RequireFields<T, K extends keyof T> = Omit<T, K> & { [P in K]-?: NonNullable<T[P]> };
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
};

export type Acceleration = {
  units?: Maybe<AccelerationUnits>;
  x?: Maybe<Array<Scalars['String']['output']>>;
  y?: Maybe<Array<Scalars['String']['output']>>;
  z?: Maybe<Array<Scalars['String']['output']>>;
};

export enum AccelerationUnits {
  Ms2 = 'ms2'
}

export type Query = {
  __typename?: 'Query';
  vehicle?: Maybe<VehicleData>;
};


export type QueryVehicleArgs = {
  vehicleId: Scalars['ID']['input'];
};

export type VehicleData = {
  __typename?: 'VehicleData';
  data?: Maybe<Acceleration>;
  log_id: Scalars['ID']['output'];
  timestamp?: Maybe<Array<Scalars['String']['output']>>;
  vehicleId: Scalars['ID']['output'];
};



export type ResolverTypeWrapper<T> = Promise<T> | T;


export type ResolverWithResolve<TResult, TParent, TContext, TArgs> = {
  resolve: ResolverFn<TResult, TParent, TContext, TArgs>;
};
export type Resolver<TResult, TParent = {}, TContext = {}, TArgs = {}> = ResolverFn<TResult, TParent, TContext, TArgs> | ResolverWithResolve<TResult, TParent, TContext, TArgs>;

export type ResolverFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => Promise<TResult> | TResult;

export type SubscriptionSubscribeFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => AsyncIterable<TResult> | Promise<AsyncIterable<TResult>>;

export type SubscriptionResolveFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => TResult | Promise<TResult>;

export interface SubscriptionSubscriberObject<TResult, TKey extends string, TParent, TContext, TArgs> {
  subscribe: SubscriptionSubscribeFn<{ [key in TKey]: TResult }, TParent, TContext, TArgs>;
  resolve?: SubscriptionResolveFn<TResult, { [key in TKey]: TResult }, TContext, TArgs>;
}

export interface SubscriptionResolverObject<TResult, TParent, TContext, TArgs> {
  subscribe: SubscriptionSubscribeFn<any, TParent, TContext, TArgs>;
  resolve: SubscriptionResolveFn<TResult, any, TContext, TArgs>;
}

export type SubscriptionObject<TResult, TKey extends string, TParent, TContext, TArgs> =
  | SubscriptionSubscriberObject<TResult, TKey, TParent, TContext, TArgs>
  | SubscriptionResolverObject<TResult, TParent, TContext, TArgs>;

export type SubscriptionResolver<TResult, TKey extends string, TParent = {}, TContext = {}, TArgs = {}> =
  | ((...args: any[]) => SubscriptionObject<TResult, TKey, TParent, TContext, TArgs>)
  | SubscriptionObject<TResult, TKey, TParent, TContext, TArgs>;

export type TypeResolveFn<TTypes, TParent = {}, TContext = {}> = (
  parent: TParent,
  context: TContext,
  info: GraphQLResolveInfo
) => Maybe<TTypes> | Promise<Maybe<TTypes>>;

export type IsTypeOfResolverFn<T = {}, TContext = {}> = (obj: T, context: TContext, info: GraphQLResolveInfo) => boolean | Promise<boolean>;

export type NextResolverFn<T> = () => Promise<T>;

export type DirectiveResolverFn<TResult = {}, TParent = {}, TContext = {}, TArgs = {}> = (
  next: NextResolverFn<TResult>,
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => TResult | Promise<TResult>;


/** Mapping of interface types */
export type ResolversInterfaceTypes<_RefType extends Record<string, unknown>> = {
  Acceleration: never;
};

/** Mapping between all available schema types and the resolvers types */
export type ResolversTypes = {
  Acceleration: ResolverTypeWrapper<ResolversInterfaceTypes<ResolversTypes>['Acceleration']>;
  AccelerationUnits: AccelerationUnits;
  Boolean: ResolverTypeWrapper<Scalars['Boolean']['output']>;
  ID: ResolverTypeWrapper<Scalars['ID']['output']>;
  Query: ResolverTypeWrapper<{}>;
  String: ResolverTypeWrapper<Scalars['String']['output']>;
  VehicleData: ResolverTypeWrapper<Omit<VehicleData, 'data'> & { data?: Maybe<ResolversTypes['Acceleration']> }>;
};

/** Mapping between all available schema types and the resolvers parents */
export type ResolversParentTypes = {
  Acceleration: ResolversInterfaceTypes<ResolversParentTypes>['Acceleration'];
  Boolean: Scalars['Boolean']['output'];
  ID: Scalars['ID']['output'];
  Query: {};
  String: Scalars['String']['output'];
  VehicleData: Omit<VehicleData, 'data'> & { data?: Maybe<ResolversParentTypes['Acceleration']> };
};

export type AccelerationResolvers<ContextType = any, ParentType extends ResolversParentTypes['Acceleration'] = ResolversParentTypes['Acceleration']> = {
  __resolveType: TypeResolveFn<null, ParentType, ContextType>;
  units?: Resolver<Maybe<ResolversTypes['AccelerationUnits']>, ParentType, ContextType>;
  x?: Resolver<Maybe<Array<ResolversTypes['String']>>, ParentType, ContextType>;
  y?: Resolver<Maybe<Array<ResolversTypes['String']>>, ParentType, ContextType>;
  z?: Resolver<Maybe<Array<ResolversTypes['String']>>, ParentType, ContextType>;
};

export type QueryResolvers<ContextType = any, ParentType extends ResolversParentTypes['Query'] = ResolversParentTypes['Query']> = {
  vehicle?: Resolver<Maybe<ResolversTypes['VehicleData']>, ParentType, ContextType, RequireFields<QueryVehicleArgs, 'vehicleId'>>;
};

export type VehicleDataResolvers<ContextType = any, ParentType extends ResolversParentTypes['VehicleData'] = ResolversParentTypes['VehicleData']> = {
  data?: Resolver<Maybe<ResolversTypes['Acceleration']>, ParentType, ContextType>;
  log_id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>;
  timestamp?: Resolver<Maybe<Array<ResolversTypes['String']>>, ParentType, ContextType>;
  vehicleId?: Resolver<ResolversTypes['ID'], ParentType, ContextType>;
  __isTypeOf?: IsTypeOfResolverFn<ParentType, ContextType>;
};

export type Resolvers<ContextType = any> = {
  Acceleration?: AccelerationResolvers<ContextType>;
  Query?: QueryResolvers<ContextType>;
  VehicleData?: VehicleDataResolvers<ContextType>;
};

