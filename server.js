import express, { request, response } from "express";
import taskRouter from './routers/tasksRouters.js'
import {connectDB} from "./config/db.py";
import dotenv from 'dotenv';

dotenv.config();
const app = express();
const PORT = process.env.PORT || 5001

app.use("/api/task", taskRouter);
app.listen(PORT, () => {
    console.log('Server bắt đầu trên cổng ${PORT}');
});
