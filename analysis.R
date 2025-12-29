library(rvest)
library(httr)
library(jsonlite)

url <- "https://www.brvm.org/fr/cours-actions/0"
ua <- "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# config(ssl_verifypeer = FALSE) bypasses the SSL issuer error
response <- GET(url, 
                add_headers(`User-Agent` = ua), 
                config(ssl_verifypeer = FALSE),
                timeout(30))

result <- list(status = "error", message = "Initialisation")

if (status_code(response) == 200) {
  page <- read_html(content(response, "text", encoding = "UTF-8"))
  table_node <- html_node(page, "table.views-table")
  
  if (!is.null(table_node)) {
    table_df <- html_table(table_node)
    
    # Cleaning the variation column (usually the 9th column)
    # Replaces ',' with '.' and removes '%' for numeric conversion
    raw_var <- table_df[[9]]
    clean_var <- as.numeric(gsub("%", "", gsub(",", ".", raw_var)))
    
    top_idx <- which.max(clean_var)
    top_stock <- table_df[top_idx, ]
    
    result <- list(
      titre = as.character(top_stock[[2]]),
      prix = paste(top_stock[[4]], "FCFA"),
      variation = as.character(top_stock[[9]]),
      status = "success"
    )
  } else {
    result$message <- "Table non trouvée sur la page"
  }
} else {
  result$message <- paste("Erreur HTTP:", status_code(response))
}

write_json(result, "temp_brvm.json", auto_unbox = TRUE)
