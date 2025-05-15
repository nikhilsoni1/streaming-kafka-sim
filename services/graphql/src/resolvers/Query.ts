import { Resolvers } from "../__generated__/resolvers-types";

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
                // 'data' will be resolved by the field resolver
            };
        },
    },
    VehicleData: {
        async data(parent, _args, _context) {
            // Assuming getAccelarationData returns an object like { x: string, y: string, z: string }
            // const accData = await _context.database.getAccelarationData({
            //     x: true,
            //     y: true,
            //     z: true,
            // });
            return await _context.database.getAccelarationData({
                x: true,
                y: true,
                z: true,
            });
        },
    },
    // VehicleData: {
    //     async data(parent, _args, _context) {
    //         // Assuming getAccelarationData returns an object like { x: string, y: string, z: string }
    //         const accData = await _context.database.getAccelarationData({
    //             x: true,
    //             y: true,
    //             z: true,
    //         });
    //         return { data: accData };
    //     },
    // },
    // Acceleration: {
    //     units(parent, _args, _context) {
    //         return AccelerationUnits.Ms2;
    //     },
    //     async x(parent, _args, _context) {
    //         // Assuming getAccelarationData returns an object like { x: string }
    //         const data = await _context.database.getAccelarationData({
    //             x: true,
    //         });
    //         return data.x;
    //     },
    //     async y(parent, _args, _context) {
    //         // Assuming getAccelarationData returns an object like { x: string }
    //         const data = await _context.database.getAccelarationData({
    //             y: true,
    //         });
    //         return data.y;
    //     },
    //     async z(parent, _args, _context) {
    //         // Assuming getAccelarationData returns an object like { x: string }
    //         const data = await _context.database.getAccelarationData({
    //             z: true,
    //         });
    //         return data.z;
    //     },
    // },
};
