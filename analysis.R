library(rvest)
library(httr)
library(jsonlite)

url <- "https://www.brvm.org/fr/cours-actions/0"
ua <- "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 1. Fetch with SSL bypass
response <- GET(url, 
                add_headers(`User-Agent` = ua), 
                config(ssl_verifypeer = FALSE),
                timeout(30))

result <- list(status = "error", titre = "BRVM", variation = "0%", prix = "---")

if (status_code(response) == 200) {
  page <- read_html(content(response, "text", encoding = "UTF-8"))
  
  # 2. Try multiple selectors to find the table
  table_node <- html_node(page, "table.views-table") # Original
  if (is.na(table_node)) table_node <- html_node(page, "table") # Fallback to first table found
  
  if (!is.na(table_node)) {
    tryCatch({
      table_df <- html_table(table_node, fill = TRUE)
      
      # BRVM structure check: usually Title is Col 2, Price Col 4, Variation Col 9
      # We use numeric indices to be safer
      raw_var <- table_df[[9]]
      clean_var <- as.numeric(gsub("%", "", gsub(",", ".", raw_var)))
      
      top_idx <- which.max(clean_var)
      
      result <- list(
        titre = as.character(table_df[top_idx, 2]),
        prix = paste(table_df[top_idx, 4], "FCFA"),
        variation = as.character(table_df[top_idx, 9]),
        status = "success"
      )
    }, error = function(e) {
      result$message <- "Parsing error"
    })
  } else {
    result$message <- "No table found on page"
  }
}

# Always write the file, even if it's the error fallback, so Python doesn't crash
write_json(result, "temp_brvm.json", auto_unbox = TRUE)
