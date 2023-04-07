import React, { useState } from "react";
import { Button } from "@mui/material";
import { shallow } from "zustand/shallow";

import useUsersStore from "../store/useUsersStore";
import { telegram } from "../App";

const Publish = () => {
  const [error, setError] = useState("");

  const { users } = useUsersStore((store) => store, shallow);

  const handlePublish = () => {
    if (!users.length) return setError("کاربران نمیتونه خالی باشه");

    for (const user of users) {
      if (!user.tasks.length)
        return setError(
          "همه کاربرانی که اضافه کرده اید، حداقل یک تسک باید داشته باشد"
        );
    }

    setError("");

    // telegram.MainButton.setText("بیلد");

    // telegram.MainButton.show();
    telegram.sendDate(users);
  };

  return (
    <div className="mt-8 mb-12">
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
