import { GraphQLResolveInfo } from "graphql";
import { AccelerationUnits, Resolvers } from "../__generated__/resolvers-types";
import { DataSourceContext } from "../types/DataSourceContext";

export const Query: Resolvers = {
    Query: {
        // thing(_parent, { id }, _context) {
        //   return { id: id.toString(), name: "Name" };
        // },
        async vehicle(_parent, { vehicleId }, _context) {
            return {
                vehicleId: vehicleId,
                log_id: "fake-log-id",
                timestamp: await _context.database.getTimestamps(),
                // data: await _context.database.getAccelarationData({
                //     x: true,
                //     y: true,
                //     z: true,
                // }),
                // 'data' will be resolved by the field resolver
            };
        },
    },
    VehicleData: {
        async data(parent, _args, _context) {
            // Here we can resolve the 'data' field if needed
            // For now, we just return the data as is
            return parent.data;
        },
    },
    Acceleration: {
        units(parent: unknown, _args: unknown, _context: unknown) {
            return AccelerationUnits.Ms2;
        },
        async x(parent, _args, _context) {
            // Assuming getAccelarationData returns an object like { x: string }
            const data = await _context.database.getAccelarationData({
                x: true,
            });
            return data.x;
        },
        async y(parent, _args, _context) {
            // Assuming getAccelarationData returns an object like { x: string }
            const data = await _context.database.getAccelarationData({
                y: true,
            });
            return data.y;
        },
        async z(parent, _args, _context) {
            // Assuming getAccelarationData returns an object like { x: string }
            const data = await _context.database.getAccelarationData({
                z: true,
            });
            return data.z;
        },
        __resolveType: function (parent: never, context: DataSourceContext, info: GraphQLResolveInfo): Promise<null> {
            throw new Error("Function not implemented.");
        }
    },
};
