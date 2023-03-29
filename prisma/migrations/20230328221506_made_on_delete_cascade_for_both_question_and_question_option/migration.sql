-- DropForeignKey
ALTER TABLE "Question" DROP CONSTRAINT "Question_question_box_id_fkey";

-- DropForeignKey
ALTER TABLE "QuestionOption" DROP CONSTRAINT "QuestionOption_question_id_fkey";

-- AddForeignKey
ALTER TABLE "Question" ADD CONSTRAINT "Question_question_box_id_fkey" FOREIGN KEY ("question_box_id") REFERENCES "QuestionsBox"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "QuestionOption" ADD CONSTRAINT "QuestionOption_question_id_fkey" FOREIGN KEY ("question_id") REFERENCES "Question"("id") ON DELETE CASCADE ON UPDATE CASCADE;
