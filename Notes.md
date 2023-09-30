# Notes

## Getting responses

1. Start Response Export

   https://yul1.qualtrics.com/API/v3/surveys/{surveyId}/export-responses

   Get the following json response.  Check every few seconds until status

   ```
   {
     "result": {
       "progressId": "ES_0MQuAZTOAp3ZLee",
       "percentComplete": 0,
       "status": "inProgress"
     },
     "meta": {
       "requestId": "3f78f8cc-069a-43c2-8277-24799f8cd6b7",
       "httpStatus": "200 - OK"
     }
   }
   ```

```
{
  "result": {
    "fileId": "c77724b1-b9f9-4e84-9f07-b9790e6d3042-def",
    "percentComplete": 100,
    "status": "complete"
  },
  "meta": {
    "requestId": "d0adf86e-5c8d-4146-8c60-99bdfc40b9ba",
    "httpStatus": "200 - OK"
  }
}
```
