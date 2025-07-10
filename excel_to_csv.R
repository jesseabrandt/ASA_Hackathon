if (!require(pacman)) {install.packages("pacman"); require(pacman)}
#library(readxl)
#library(tidyverse, warn.conflicts = FALSE)
pacman::p_load(readxl, tidyverse)

files <- Sys.glob("Patient X data files/*.xlsx") |>
  grep(pattern = "~", invert = T, value = T)

#Numerical Data
#TODO: handle duplicates

#function to read a sheet from each file
read_numerical_sheet <- function(sheet, suffix){
  df <- map(files, \(x) tryCatch({
    read_excel(x, sheet = sheet)},
    error = function(msg){
      return(data.frame())
    }
    )) %>%
    bind_rows() %>%
    #mutate(across(-Date, parse_number)) %>%
    group_by(Date) %>% #handle duplicates
    summarize(Min = min(Min), Max = max(Max), Avg = mean(Avg), Median = median(Median)) %>%
    rename_with(~paste0(.x, paste0(" ", suffix)), -Date)
  return(df)
}

heart_rate <- read_numerical_sheet("Heart Rate","Heart Rate")
oxygen_level <- read_numerical_sheet("Oxygen Level", "Oxygen Level")
breathing_rate <- read_numerical_sheet("Breathing Rate", "Breathing Rate")
#why are there two values? so I can later make this function work for sleep too

#function won't work for sleep - different values
sleep <- map(files, \(x)read_excel(x, sheet = "Sleep")) %>%
  bind_rows()%>%
  mutate(across(Light:Total, parse_number)) %>%
  group_by(Date) %>% #handle duplicates
  summarize(across(Light:Total, mean)) %>%
  rename_with(~paste0(.x, " Sleep Observation"), -Date)

breathing_rate <- map(files, \(x)read_excel(x, sheet = "Breathing Rate")) %>%
  bind_rows() %>%
  #mutate(across(-Date, parse_number)) %>%
  group_by(Date) %>% #handle duplicates
  summarize(
    Min = min(Min), Max = max(Max), 
    Avg = mean(Avg), Median = median(Median)) %>%
  rename_with(~paste0(.x, " Breathing Rate"), -Date) 

numerical_data <- breathing_rate %>%
  full_join(heart_rate) %>%
  full_join(oxygen_level) %>%
  full_join(sleep)

write_csv(numerical_data, "data/numerical_data.csv")

#Text Data
#sleep activities should go in table with observations and activities
sleep_activities <- map(files, \(x)read_excel(x, sheet = "Sleep Activities")) %>%
  bind_rows() %>%
  mutate(Category = "Sleep Activity")
observations <- map(files, \(x)read_excel(x, sheet = "Observations")) %>%
  bind_rows() %>%
  mutate(Category = "Observation")
activities <- map(files, \(x)read_excel(x, sheet = "Activities")) %>%
  bind_rows()

text_data <- bind_rows(sleep_activities, observations, activities)
write_csv(text_data, "data/text_data.csv")

all_data <- full_join(text_data, numerical_data)
write_csv(all_data, "data/full_dataset.csv")
