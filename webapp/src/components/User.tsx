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
  nickname: string;
  username: string;
  onDelete: (username: string) => void;
}

const User: React.FC<UserProps> = ({ nickname, username, onDelete }) => {
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
    <div className="border md:px-12 px-8 md:py-8 py-6 rounded-xl">
      <h3 className="mb-5 font-extrabold md:text-xl text-lg text-right">
        {nickname}
      </h3>

      <div className="flex items-center justify-between rounded-lg mb-6 border md:px-6 px-4 py-2">
        <p>
          <span className="hidden md:inline">نام کاربری: </span>
          <span>{username}</span>
        </p>

        <Button
          size="small"
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
