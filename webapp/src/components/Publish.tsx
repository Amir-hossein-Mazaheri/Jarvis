import React, { useRef, useState } from "react";
import { Button } from "@mui/material";
import { shallow } from "zustand/shallow";

import useUsersStore from "../store/useUsersStore";
import { telegram } from "../App";
import useTasksStore from "../store/useTasksStore";

const Publish = () => {
  const [error, setError] = useState("");
  const [show, setShow] = useState(false);

  const downloadBtnRef = useRef<HTMLAnchorElement>(null);

  const { users } = useUsersStore((store) => store, shallow);
  const { all, tasks } = useTasksStore((store) => store, shallow);

  const handlePublish = () => {
    if (all === "specified") {
      if (!users.length) return setError("کاربران نمیتونه خالی باشه");

      for (const user of users) {
        if (!user.tasks.length)
          return setError(
            "همه کاربرانی که اضافه کرده اید، حداقل یک تسک باید داشته باشد"
          );
      }
    } else {
      if (!tasks.length) return setError("حداقل یک تسک باید اضافه کنید");
    }

    setError("");
    setShow(true);

    if (downloadBtnRef.current) {
      downloadBtnRef.current.href = `data:application/json;charset:utf-8,${JSON.stringify(
        all === "all" ? { tasks } : users
      )}`;
      downloadBtnRef.current.download = "tasks.json";

      downloadBtnRef.current.click();
    }

    telegram.sendData({
      data: users,
    });
  };

  return (
    <div className="mt-8 mb-12">
      <div className="hidden">
        <a ref={downloadBtnRef}></a>
      </div>

      <div>
        <Button
          fullWidth
          variant="contained"
          color="info"
          size="large"
          onClick={handlePublish}
        >
          آماده سازی
        </Button>
      </div>
      {!!error && <div className="font-bold text-red-500 mt-5">{error}</div>}
    </div>
  );
};

export default Publish;
