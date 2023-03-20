/*
  Warnings:

  - You are about to drop the column `c_user_id` on the `Question` table. All the data in the column will be lost.
  - You are about to drop the column `deadline` on the `Question` table. All the data in the column will be lost.
  - You are about to drop the column `w_user_id` on the `Question` table. All the data in the column will be lost.

*/
-- DropForeignKey
ALTER TABLE "Question" DROP CONSTRAINT "Question_c_user_id_fkey";

-- DropForeignKey
ALTER TABLE "Question" DROP CONSTRAINT "Question_w_user_id_fkey";

-- AlterTable
ALTER TABLE "Question" DROP COLUMN "c_user_id",
DROP COLUMN "deadline",
DROP COLUMN "w_user_id",
ADD COLUMN     "question_box_id" INTEGER;

-- CreateTable
CREATE TABLE "QuestionsBox" (
    "id" SERIAL NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deadline" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "QuestionsBox_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "_correct_questions" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "_wrong_questions" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "_QuestionsBoxToUser" (
    "A" INTEGER NOT NULL,
    "B" INTEGER NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "_correct_questions_AB_unique" ON "_correct_questions"("A", "B");

-- CreateIndex
CREATE INDEX "_correct_questions_B_index" ON "_correct_questions"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_wrong_questions_AB_unique" ON "_wrong_questions"("A", "B");

-- CreateIndex
CREATE INDEX "_wrong_questions_B_index" ON "_wrong_questions"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_QuestionsBoxToUser_AB_unique" ON "_QuestionsBoxToUser"("A", "B");

-- CreateIndex
CREATE INDEX "_QuestionsBoxToUser_B_index" ON "_QuestionsBoxToUser"("B");

-- AddForeignKey
ALTER TABLE "Question" ADD CONSTRAINT "Question_question_box_id_fkey" FOREIGN KEY ("question_box_id") REFERENCES "QuestionsBox"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_correct_questions" ADD CONSTRAINT "_correct_questions_A_fkey" FOREIGN KEY ("A") REFERENCES "Question"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_correct_questions" ADD CONSTRAINT "_correct_questions_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_wrong_questions" ADD CONSTRAINT "_wrong_questions_A_fkey" FOREIGN KEY ("A") REFERENCES "Question"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_wrong_questions" ADD CONSTRAINT "_wrong_questions_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_QuestionsBoxToUser" ADD CONSTRAINT "_QuestionsBoxToUser_A_fkey" FOREIGN KEY ("A") REFERENCES "QuestionsBox"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_QuestionsBoxToUser" ADD CONSTRAINT "_QuestionsBoxToUser_B_fkey" FOREIGN KEY ("B") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
