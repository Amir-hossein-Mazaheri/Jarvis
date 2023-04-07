import React from "react";
import { Task as T } from "../store/useUsersStore";
import { Button } from "@mui/material";

interface TaskProps extends T {
  onDelete: (task: T) => void;
}

const Task: React.FC<TaskProps> = (task) => {
  const { job, weight, deadline, onDelete } = task;

  return (
    <div className="relative px-6 py-4 rounded-xl shadow">
      <div className="mb-4 text-xl font-bold flex items-center justify-between">
        <h2>{job}</h2>

        <Button variant="outlined" color="error" onClick={() => onDelete(task)}>
          حذف تسک
        </Button>
      </div>

      <div className="flex items-center justify-between">
        <p>
          <span>وزن تسک: </span>
          <span>{weight}</span>
        </p>

        <p>
          <span>{deadline} </span>
          <span>روز تا ددلاین</span>
        </p>
      </div>
    </div>
  );
};

export default Task;
