/*
  Warnings:

  - You are about to drop the column `createdAt` on the `QuestionsBox` table. All the data in the column will be lost.
  - You are about to drop the column `createdAt` on the `Task` table. All the data in the column will be lost.
  - You are about to drop the column `markDone` on the `Task` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "QuestionsBox" DROP COLUMN "createdAt",
ADD COLUMN     "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- AlterTable
ALTER TABLE "Task" DROP COLUMN "createdAt",
DROP COLUMN "markDone",
ADD COLUMN     "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "mark_done" BOOLEAN NOT NULL DEFAULT false;
