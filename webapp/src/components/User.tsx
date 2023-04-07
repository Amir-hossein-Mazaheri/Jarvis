import React, { useMemo } from "react";
import { shallow } from "zustand/shallow";
import { Controller, SubmitHandler, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import z from "zod";
import { TextField, Button } from "@mui/material";

import { Task as T } from "../store/useUsersStore";
import useUsersStore from "../store/useUsersStore";
import Task from "./Task";

interface UserProps {
  username: string;
  onDelete: (username: string) => void;
}

const addTaskSchema = z.object({
  job: z.string().min(1),
  weight: z.preprocess((value) => Number(value), z.number().positive()),
  deadline: z.preprocess((value) => Number(value), z.number().positive()),
});

const User: React.FC<UserProps> = ({ username, onDelete }) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<z.infer<typeof addTaskSchema>>({
    resolver: zodResolver(addTaskSchema),
  });

  const { users, addTask, removeTask } = useUsersStore(
    (store) => store,
    shallow
  );

  const getUserTasks = useMemo(
    () => users.find((u) => u.username === username)?.tasks,
    [users, username]
  );

  const handleAddTask: SubmitHandler<z.infer<typeof addTaskSchema>> = (
    data
  ) => {
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

      <div>
        <form className="space-y-8" onSubmit={handleSubmit(handleAddTask)}>
          <Controller
            name="job"
            control={control}
            render={({ field }) => (
              <TextField
                {...field}
                fullWidth
                id="job"
                label="تسکت چیه..."
                variant="standard"
                error={!!errors["job"]}
                helperText={errors["job"]?.message?.toString()}
              />
            )}
          />

          <div className="flex items-center gap-8">
            <Controller
              name="weight"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  id="weight"
                  label="وزن تسک چقدره..."
                  variant="standard"
                  error={!!errors["weight"]}
                  helperText={errors["weight"]?.message?.toString()}
                />
              )}
            />

            <Controller
              name="deadline"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  id="deadline"
                  type="number"
                  label="ددلاین تسک چن روز دیگه اس..."
                  variant="standard"
                  error={!!errors["deadline"]}
                  helperText={errors["deadline"]?.message?.toString()}
                />
              )}
            />
          </div>

          <div className="flex items-center justify-end">
            <Button variant="contained" type="submit">
              افزودن تسک
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default User;
