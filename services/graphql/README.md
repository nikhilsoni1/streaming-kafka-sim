# Simple GraphQL Example for Acceleration Data

## Setup

1. Install the [Requirements](#Requirements)

2. Open a terminal inside the directory

3. Install all required packages:

   

   ```bash
   pnpm install
   ```

4. To start the server:

   ```bash
   pnpm turbo run dev
   ```

   See [note](#Turbo) about installing Turbo as a global dependency.

During active development, it is sometimes advantageous to update the generated Typescript types that are created from the GQL schema. To run both the server and the generator to watch types, run

``` bash
pnpm turbo run dev generate:watch
```



## #Requirements:

### NodeJS

[Install link](https://nodejs.org/en/download)

### PNPM

[Recommend installeding](https://pnpm.io/installation#using-corepack) using corepack (if not installed with NodeJS)

### #Turbo*

*While not required to install globally (root Package.json is set up such that PNPM will install it as a dev dependency), installing globally allows you to drop the 'pnpm' before any turbo commands in the terminal

Link to [Turborepo Docs](https://turborepo.com/docs/getting-started/installation#installing-turbo)

