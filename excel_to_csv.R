if (!require(pacman)) {install.packages("pacman"); require(pacman)}
#library(readxl)
#library(tidyverse, warn.conflicts = FALSE)
pacman::p_load(readxl, tidyverse)

files <- Sys.glob("Patient X data files/*.xlsx") |>
  grep(pattern = "~", invert = T, value = T)

#Numerical Data
#TODO: handle duplicates
heart_rate <- map(files, \(x)read_excel(x, sheet = "Heart Rate")) %>%
  bind_rows() %>%
  #mutate(across(-Date, parse_number)) %>%
  group_by(Date) %>% #handle duplicates
  summarize(Min = min(Min), Max = max(Max), Avg = mean(Avg), Median = median(Median)) %>%
  rename_with(~paste0(.x, " Heart Rate"), -Date)
sleep <- map(files, \(x)read_excel(x, sheet = "Sleep")) %>%
  bind_rows()%>%
  mutate(across(Light:Total, parse_number)) %>%
  group_by(Date) %>% #handle duplicates
  summarize(across(Light:Total, mean)) %>%
  rename_with(~paste0(.x, " Sleep Observation"), -Date)
oxygen_level <- map(files, \(x)tryCatch({read_excel(x, sheet = "Oxygen Level")},
                                        error = function(msg){
                                          return(data.frame())
                                        })) %>%
  bind_rows() %>%
  #mutate(across(-Date, parse_number)) %>%
  group_by(Date) %>% #handle duplicates
  summarize(Min = min(Min), Max = max(Max), Avg = mean(Avg), Median = median(Median))  %>%
  rename_with(~paste0(.x, " Oxygen Level"), -Date)
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

write_csv(numerical_data, "numerical_data.csv")

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
write_csv(text_data, "text_data.csv")
