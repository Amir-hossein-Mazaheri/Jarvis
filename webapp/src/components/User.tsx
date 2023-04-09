import React, { useMemo } from "react";
import { shallow } from "zustand/shallow";
import { Controller, SubmitHandler, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import z from "zod";
import { TextField, Button } from "@mui/material";

import { Task as T } from "../store/useUsersStore";
import useUsersStore from "../store/useUsersStore";
import Task from "./Task";
import AddTaskForm, { AddTaskOnSubmit } from "./AddTaskForm";

interface UserProps {
  username: string;
  onDelete: (username: string) => void;
}

const User: React.FC<UserProps> = ({ username, onDelete }) => {
  const { users, addTask, removeTask } = useUsersStore(
    (store) => store,
    shallow
  );

  const getUserTasks = useMemo(
    () => users.find((u) => u.username === username)?.tasks,
    [users, username]
  );

  const handleAddTask: AddTaskOnSubmit = (data) => {
    addTask(username, data);
  };

  const handleDeleteTask = (task: T) => {
    removeTask(username, task);
  };

  return (
    <div className="border px-12 py-8 rounded-xl">
      <div className="flex items-center justify-between rounded-lg mb-6 border px-6 py-2">
        <p>
          <span>نام کاربری: </span>
          <span>{username}</span>
        </p>

        <Button
          variant="outlined"
          color="error"
          onClick={() => onDelete(username)}
        >
          حذف کاربر
        </Button>
      </div>

      <div className="mt-6 mb-12 space-y-6">
        {getUserTasks?.map((task) => (
          <Task
            key={JSON.stringify(task)}
            onDelete={handleDeleteTask}
            {...task}
          />
        ))}
      </div>

      <AddTaskForm onSubmit={handleAddTask} />
    </div>
  );
};

export default User;
