library(rvest)
library(jsonlite)

# Fetch BRVM Data
url <- "https://www.brvm.org/fr/cours-actions/0"
page <- read_html(url)
table_node <- html_node(page, "table.views-table")

if (!is.null(table_node)) {
  # Convert HTML table to Data Frame
  df <- html_table(table_node)
  
  # Clean the Variation column (9th column) to find the best performer
  # Remove %, replace comma with dot, and convert to numeric
  df$var_numeric <- as.numeric(gsub("%", "", gsub(",", ".", df[[9]])))
  
  # Identify the top performer
  top_row <- df[which.max(df$var_numeric), ]
  
  # Prepare temporary data for Python
  extracted <- list(
    titre = top_row[[2]],
    prix = paste(top_row[[4]], "FCFA"),
    variation = top_row[[9]]
  )
  
  # Save to a temp file
  write_json(extracted, "temp_brvm.json", auto_unbox = TRUE)
}
