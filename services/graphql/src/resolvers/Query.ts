import { Resolvers } from "../__generated__/resolvers-types";

export const Query: Resolvers = {
    Query: {
        // thing(_parent, { id }, _context) {
        //   return { id: id.toString(), name: "Name" };
        // },
        vehicle(_parent, { vehicleId }, _context) {
            return {
                vehicleId: vehicleId,
                log_id: "something",
                timestamp: [],
                // 'data' will be resolved by the field resolver
            };
        },
    },
    // VehicleData: {
    //     data: () => Promise.resolve({
    //         units: "ms2",
    //         x: [1, 2, 3],
    //         y: [1, 2, 3],
    //         z: [1, 2, 3],
    //     }),
    // },
};
