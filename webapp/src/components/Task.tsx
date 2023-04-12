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
      <div className="mb-4 flex md:flex-row flex-col gap-6 items-center justify-between">
        <h2 className="text-sm md:text-xl font-bold">{job}</h2>

        <Button
          className="md:w-fit w-full"
          variant="outlined"
          color="error"
          onClick={() => onDelete(task)}
        >
          حذف تسک
        </Button>
      </div>

      <div className="flex md:flex-row flex-col gap-3 items-center justify-between">
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
