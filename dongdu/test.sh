#!/bin/bash
vlsp_test_data="/home/longbb/graduation-project/word_recognition/VLSP_Sentences/test_100_articles"
for file in "$vlsp_test_data"/*;
do
  original_file_name=${file##*/}
  new_nunber=(${original_file_name//./})
  output_file="test_dongdu/$new_nunber.txt"
  predict_command="./predictor -i $file -o $output_file"
  echo $predict_command
  eval $predict_command
done
