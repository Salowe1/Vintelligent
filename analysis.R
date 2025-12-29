# analysis.R
library(rvest)
library(httr)
library(jsonlite)

url <- "https://www.brvm.org/fr/cours-actions/0"

# Set a browser user-agent to bypass the connection block
ua <- "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# Fetch page with headers
response <- GET(url, add_headers(`User-Agent` = ua))

if (status_code(response) == 200) {
  page <- read_html(content(response, "text"))
  table_df <- html_table(html_node(page, "table.views-table"))
  
  # Clean and parse variation
  table_df$Variation_Num <- as.numeric(gsub("%", "", gsub(",", ".", table_df[[9]])))
  top_stock <- table_df[which.max(table_df$Variation_Num), ]
  
  result <- list(
    titre = top_stock[[2]],
    prix = paste(top_stock[[4]], "FCFA"),
    variation = top_stock[[9]],
    status = "success"
  )
} else {
  result <- list(status = "error", message = paste("HTTP Error:", status_code(response)))
}

write_json(result, "temp_brvm.json", auto_unbox = TRUE)
