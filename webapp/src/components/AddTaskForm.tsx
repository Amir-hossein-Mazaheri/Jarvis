import { zodResolver } from "@hookform/resolvers/zod";
import { Button, TextField } from "@mui/material";
import React from "react";
import { Controller, SubmitHandler, useForm } from "react-hook-form";
import { z } from "zod";

export const addTaskSchema = z.object({
  job: z.string().min(1),
  weight: z.preprocess((value) => Number(value), z.number().positive()),
  deadline: z.preprocess((value) => Number(value), z.number().positive()),
});

export type AddTaskOnSubmit = SubmitHandler<z.infer<typeof addTaskSchema>>;

interface AddTaskFormProps {
  onSubmit: AddTaskOnSubmit;
}

const AddTaskForm: React.FC<AddTaskFormProps> = ({ onSubmit }) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<z.infer<typeof addTaskSchema>>({
    resolver: zodResolver(addTaskSchema),
  });

  return (
    <div>
      <form className="space-y-8" onSubmit={handleSubmit(onSubmit)}>
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

        <div className="flex md:flex-row flex-col items-center gap-8">
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
          <Button variant="contained" type="submit" className="w-full lg:w-fit">
            افزودن تسک
          </Button>
        </div>
      </form>
    </div>
  );
};

export default AddTaskForm;
