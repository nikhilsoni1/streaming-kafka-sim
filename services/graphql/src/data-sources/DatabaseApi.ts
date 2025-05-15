import path from "path";
import {
    Acceleration,
    AccelerationUnits,
    VehicleData,
} from "../__generated__/resolvers-types";

export class DatabaseAPI {
    // private readonly url: string;
    // private readonly auth: string | undefined;

    constructor() {
        // this.url = process.env.DATABASE_URL ?? "";
        // this.auth = process.env.DATABASE_AUTH;
    }

    public async getTimestamps() {
        const filePath = path.resolve(__dirname, "../../../mocks/data.json");
        const { readFile } = await import("fs/promises");
        const fileContent = await readFile(filePath, { encoding: "utf-8" });
        const json = JSON.parse(fileContent);

        return json.data.timestamp as VehicleData["timestamp"];
    }

    public async getAccelarationData({
        x = false,
        y = false,
        z = false,
    }: {
        x?: boolean;
        y?: boolean;
        z?: boolean;
    }) {
        const filePath = path.resolve(__dirname, "../../../mocks/data.json");
        const { readFile } = await import("fs/promises");
        const fileContent = await readFile(filePath, { encoding: "utf-8" });
        const json = JSON.parse(fileContent);

        // Optionally filter axes based on args
        let result = {
            units: AccelerationUnits.Ms2,
            x: x ? (json.data.acceleration["x:"] as [string]) : undefined,
            y: y ? (json.data.acceleration["y:"] as [string]) : undefined,
            z: z ? (json.data.acceleration["z:"] as [string]) : undefined,
        };

        return result as Acceleration;
    }
}
