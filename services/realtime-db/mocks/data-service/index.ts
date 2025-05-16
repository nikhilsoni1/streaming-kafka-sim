import { faker } from "@faker-js/faker";
import express from "express";
import _ from "lodash";

const app = express();
app.get("/", (req, res) => {
    res.send({
        message: "Visit /address to get random address data.",
    });
});

app.get("/address", (req, res) => {
    const count = req.query.count;
    if (!count) {
        return res
            .status(400)
            .send({ errorMsg: "count query parameter is missing." });
    }
    res.send(
        // @ts-ignore
        _.times(count, () => {
            const address = faker.location;
            return {
                country: address.country(),
                city: address.city(),
                state: address.state(),
                zipCode: address.zipCode(),
                latitude: address.latitude(),
                longitude: address.longitude(),
            };
        })
    );
});

app.listen(3030, () => {
    console.info("🚀 Mock server started at http://localhost:3030");
});
